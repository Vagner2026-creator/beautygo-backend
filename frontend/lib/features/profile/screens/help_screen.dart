import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  static const _faqs = [
    _Faq(
      question: 'Como faço um agendamento?',
      answer:
          'Busque um profissional na tela inicial ou na busca, clique no perfil dele e escolha um serviço. Selecione a data e o horário disponíveis e confirme o agendamento.',
    ),
    _Faq(
      question: 'Como cancelo um agendamento?',
      answer:
          'Acesse a tela "Agendamentos", localize o agendamento ativo e toque em "Cancelar". O cancelamento é gratuito até 2 horas antes do horário marcado.',
    ),
    _Faq(
      question: 'Como entro em contato com o profissional?',
      answer:
          'Após confirmar um agendamento, o telefone do profissional fica disponível nos detalhes do agendamento.',
    ),
    _Faq(
      question: 'Meu pagamento é seguro?',
      answer:
          'Sim. Todos os pagamentos são processados por gateways certificados PCI-DSS. O BeautyGO nunca armazena dados do cartão.',
    ),
    _Faq(
      question: 'Como avalio um profissional?',
      answer:
          'Após a conclusão de um atendimento, você recebe uma notificação para deixar sua avaliação. Você também pode avaliar na tela de histórico de agendamentos.',
    ),
    _Faq(
      question: 'Como me torno um profissional parceiro?',
      answer:
          'Faça o registro escolhendo o perfil "Profissional". Complete seu cadastro com serviços, disponibilidade e local de atendimento. Nossa equipe revisará e ativará sua conta em até 24 horas.',
    ),
    _Faq(
      question: 'Esqueci minha senha, o que faço?',
      answer:
          'Na tela de login, toque em "Esqueci minha senha" e informe seu e-mail. Você receberá um link para criar uma nova senha.',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ajuda e FAQ')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const SizedBox(height: 8),
          const Text(
            'Perguntas frequentes',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          const Text(
            'Encontre respostas para as dúvidas mais comuns.',
            style: TextStyle(color: AppTheme.textSecondary, fontSize: 13),
          ),
          const SizedBox(height: 16),
          ..._faqs.map((faq) => _FaqTile(faq: faq)),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.primary.withOpacity(0.08),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.support_agent, color: AppTheme.primary),
                    SizedBox(width: 8),
                    Text(
                      'Ainda precisa de ajuda?',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                const Text(
                  'Entre em contato com nosso suporte:',
                  style: TextStyle(color: AppTheme.textSecondary, fontSize: 13),
                ),
                const SizedBox(height: 6),
                const Row(
                  children: [
                    Icon(Icons.email_outlined, size: 16, color: AppTheme.textSecondary),
                    SizedBox(width: 6),
                    Text(
                      'suporte@beautygo.com.br',
                      style: TextStyle(
                        color: AppTheme.primary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                const Row(
                  children: [
                    Icon(Icons.access_time, size: 16, color: AppTheme.textSecondary),
                    SizedBox(width: 6),
                    Text(
                      'Seg–Sex, 9h às 18h',
                      style: TextStyle(color: AppTheme.textSecondary, fontSize: 13),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }
}

class _Faq {
  final String question;
  final String answer;
  const _Faq({required this.question, required this.answer});
}

class _FaqTile extends StatelessWidget {
  final _Faq faq;
  const _FaqTile({required this.faq});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 0,
      color: Colors.white,
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        iconColor: AppTheme.primary,
        collapsedIconColor: AppTheme.textSecondary,
        title: Text(
          faq.question,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            faq.answer,
            style: const TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 14,
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }
}
