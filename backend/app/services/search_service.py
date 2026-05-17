from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.professional import Professional
from app.models.professional_service import ProfessionalService
from app.models.city import City
from app.models.search_log import SearchLog
from app.repositories.professional_repository import ProfessionalRepository
from app.schemas.professional import ProfessionalResponse
from app.schemas.search import SearchFilters
from app.core.utils import haversine_distance


class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.pro_repo = ProfessionalRepository(db)

    def search(
        self,
        filters: SearchFilters,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
    ) -> dict:
        query = (
            self.db.query(Professional)
            .options(joinedload(Professional.user), joinedload(Professional.city))
            .filter(Professional.is_available == True)
        )

        # Keyword search across multiple fields and service names
        if filters.keyword:
            kw = f"%{filters.keyword}%"
            service_subquery = (
                self.db.query(ProfessionalService.professional_id)
                .filter(ProfessionalService.name.ilike(kw))
                .filter(ProfessionalService.is_active == True)
                .subquery()
            )
            query = query.filter(
                or_(
                    Professional.business_name.ilike(kw),
                    Professional.description.ilike(kw),
                    Professional.specialty.ilike(kw),
                    Professional.neighborhood.ilike(kw),
                    Professional.id.in_(service_subquery),
                )
            )

        if filters.city_id:
            query = query.filter(Professional.city_id == filters.city_id)

        if filters.state_id:
            query = query.join(City, Professional.city_id == City.id).filter(
                City.state_id == filters.state_id
            )

        if filters.neighborhood:
            query = query.filter(Professional.neighborhood.ilike(f"%{filters.neighborhood}%"))

        if filters.home_service is not None:
            query = query.filter(Professional.home_service == filters.home_service)

        if filters.salon_service is not None:
            query = query.filter(Professional.salon_service == filters.salon_service)

        if filters.min_rating is not None:
            query = query.filter(Professional.rating >= filters.min_rating)

        # Price filter via services
        if filters.category_id is not None or filters.min_price is not None or filters.max_price is not None:
            service_query = self.db.query(ProfessionalService.professional_id).filter(
                ProfessionalService.is_active == True
            )
            if filters.category_id is not None:
                service_query = service_query.filter(
                    ProfessionalService.category_id == filters.category_id
                )
            if filters.min_price is not None:
                service_query = service_query.filter(ProfessionalService.price >= filters.min_price)
            if filters.max_price is not None:
                service_query = service_query.filter(ProfessionalService.price <= filters.max_price)
            subq = service_query.subquery()
            query = query.filter(Professional.id.in_(subq))

        total = query.count()
        skip = (filters.page - 1) * filters.size

        if user_lat is not None and user_lng is not None:
            # Fetch all (no DB-level pagination) to sort by distance
            professionals = query.all()
            results_with_distance = []
            for p in professionals:
                if p.latitude is not None and p.longitude is not None:
                    dist = haversine_distance(user_lat, user_lng, float(p.latitude), float(p.longitude))
                else:
                    dist = None

                if filters.max_distance_km is not None and (dist is None or dist > filters.max_distance_km):
                    continue

                item = ProfessionalResponse.model_validate(p).model_dump()
                item["distance_km"] = round(dist, 2) if dist is not None else None
                results_with_distance.append(item)

            results_with_distance.sort(
                key=lambda x: (x["distance_km"] is None, x["distance_km"] or 0)
            )
            total = len(results_with_distance)
            items = results_with_distance[skip: skip + filters.size]
        else:
            professionals = (
                query.order_by(Professional.rating.desc(), Professional.business_name)
                .offset(skip)
                .limit(filters.size)
                .all()
            )
            items = [ProfessionalResponse.model_validate(p).model_dump() for p in professionals]

        return {"items": items, "total": total, "page": filters.page, "size": filters.size}

    def log_search(self, user_id: Optional[int], keyword: Optional[str], city_id: Optional[int]) -> None:
        log = SearchLog(user_id=user_id, keyword=keyword, city_id=city_id)
        self.db.add(log)
        self.db.commit()
