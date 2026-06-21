import 'package:flutter/material.dart';
import 'package:multimedia_summary/models/summary_model.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:share_plus/share_plus.dart';
import 'package:intl/intl.dart';

class ResultScreen extends StatelessWidget {
  final FullResult result;

  const ResultScreen({required this.result, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📋 요약 결과'),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 메타데이터
            _buildMetadata(context),
            const SizedBox(height: 24),

            // 요약
            _buildSummary(context),
            const SizedBox(height: 24),

            // 인사이트
            _buildInsights(context),
            const SizedBox(height: 24),

            // 카테고리
            if (result.summary.categories.isNotEmpty)
              _buildCategories(context),
            const SizedBox(height: 24),

            // 주식 관련
            if (result.summary.stockRelated?.isNotEmpty ?? false)
              _buildStockRelated(context),
            const SizedBox(height: 24),

            // 배포 상태
            _buildDistributionStatus(context),
            const SizedBox(height: 24),

            // 버튼들
            _buildActions(context),
          ],
        ),
      ),
    );
  }

  Widget _buildMetadata(BuildContext context) {
    final metadata = result.summary.metadata;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              metadata.title,
              style: Theme.of(context).textTheme.titleLarge,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),
            if (metadata.channel != null)
              Text(
                '채널: ${metadata.channel}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () => _launchUrl(metadata.url),
              child: Text(
                '원본 링크',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.primary,
                  decoration: TextDecoration.underline,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummary(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '📝 요약',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              result.summary.summary,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildInsights(BuildContext context) {
    final insights = result.summary.keyInsights;
    if (insights.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '💡 주요 인사이트',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ...insights.map((insight) => Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Padding(
                padding: EdgeInsets.only(top: 4, right: 8),
                child: Text('•'),
              ),
              Expanded(child: Text(insight)),
            ],
          ),
        )),
      ],
    );
  }

  Widget _buildCategories(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '🏷️ 카테고리',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: result.summary.categories.map((cat) {
            final colors = _getCategoryColor(cat);
            return Chip(
              label: Text(cat),
              backgroundColor: colors['bg'],
              labelStyle: TextStyle(color: colors['text']),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildStockRelated(BuildContext context) {
    final stock = result.summary.stockRelated;
    if (stock == null || stock.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '💰 자본/주식 관련',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: Colors.orange,
          ),
        ),
        const SizedBox(height: 12),
        Card(
          color: Colors.orange.shade50,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: stock.map((item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Padding(
                      padding: EdgeInsets.only(top: 4, right: 8),
                      child: Text('📈'),
                    ),
                    Expanded(child: Text(item)),
                  ],
                ),
              )).toList(),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDistributionStatus(BuildContext context) {
    final dist = result.distribution;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '📤 배포 상태',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _DistributionItem(
              icon: Icons.mail,
              label: 'Gmail',
              status: dist.emailSent,
            ),
            const SizedBox(height: 8),
            _DistributionItem(
              icon: Icons.description,
              label: 'Obsidian',
              status: dist.obsidianSaved,
            ),
            const SizedBox(height: 8),
            _DistributionItem(
              icon: Icons.language,
              label: 'GitHub Pages',
              status: dist.githubPagesUpdated,
            ),
            if (dist.errors.isNotEmpty) ...[
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 12),
              Text(
                '오류:',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.red,
                ),
              ),
              ...dist.errors.map((e) => Text(
                '• $e',
                style: const TextStyle(fontSize: 12, color: Colors.red),
              )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildActions(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () => Share.share(
              '📺 ${result.summary.metadata.title}\n\n${result.summary.summary}\n\n링크: ${result.summary.metadata.url}',
            ),
            icon: const Icon(Icons.share),
            label: const Text('공유'),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(Icons.arrow_back),
            label: const Text('돌아가기'),
          ),
        ),
      ],
    );
  }

  Future<void> _launchUrl(String url) async {
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url));
    }
  }

  Map<String, Color> _getCategoryColor(String category) {
    switch (category.toUpperCase()) {
      case 'AI':
      case 'MACHINE LEARNING':
        return {'bg': Colors.purple.shade100, 'text': Colors.purple};
      case 'STOCK':
      case 'CAPITAL':
        return {'bg': Colors.orange.shade100, 'text': Colors.orange};
      case 'LEARNING':
      case 'EDUCATION':
        return {'bg': Colors.blue.shade100, 'text': Colors.blue};
      default:
        return {'bg': Colors.grey.shade100, 'text': Colors.grey};
    }
  }
}

class _DistributionItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool status;

  const _DistributionItem({
    required this.icon,
    required this.label,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 20),
        const SizedBox(width: 12),
        Expanded(child: Text(label)),
        Icon(
          status ? Icons.check_circle : Icons.schedule,
          color: status ? Colors.green : Colors.orange,
          size: 20,
        ),
      ],
    );
  }
}
