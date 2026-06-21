import 'package:flutter/material.dart';
import 'package:multimedia_summary/screens/result_screen.dart';
import 'package:multimedia_summary/screens/loading_screen.dart';
import 'package:multimedia_summary/services/api_service.dart';
import 'package:multimedia_summary/services/clipboard_helper.dart';
import 'package:multimedia_summary/models/summary_model.dart';
import 'package:provider/provider.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late TextEditingController _urlController;
  bool _isLoading = false;
  String _loadingStatus = '';
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController();
    _loadClipboardUrl();
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  /// 클립보드에서 URL 자동 감지
  Future<void> _loadClipboardUrl() async {
    try {
      final url = await ClipboardHelper.getClipboardText();
      if (url != null && _isValidUrl(url)) {
        setState(() {
          _urlController.text = url;
        });
      }
    } catch (e) {
      // 클립보드 접근 실패 무시
    }
  }

  /// URL 유효성 검사
  bool _isValidUrl(String url) {
    try {
      final uri = Uri.parse(url);
      return uri.scheme == 'http' || uri.scheme == 'https';
    } catch (e) {
      return false;
    }
  }

  /// 요약 생성
  Future<void> _summarize() async {
    final url = _urlController.text.trim();

    if (url.isEmpty) {
      _showError('링크를 입력해주세요');
      return;
    }

    if (!_isValidUrl(url)) {
      _showError('유효한 링크가 아닙니다');
      return;
    }

    setState(() {
      _isLoading = true;
      _loadingStatus = 'AI 요약 중...';
      _errorMessage = null;
    });

    try {
      // Gemini가 서버에서 YouTube 직접 접근 — 앱은 URL만 전송
      final apiService = context.read<ApiService>();
      final result = await apiService.summarizeVideo(
        videoUrl: url,
      );

      if (mounted) {
        // 결과 화면으로 이동
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => ResultScreen(result: result),
          ),
        );
      }
    } catch (e) {
      _showError('요약 생성 실패: $e');
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _showError(String message) {
    setState(() => _errorMessage = message.length > 80 ? '${message.substring(0, 80)}...' : message);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('오류'),
        content: SingleChildScrollView(child: SelectableText(message)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('확인')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📺 Multimedia Summary'),
        elevation: 0,
        centerTitle: true,
      ),
      body: _isLoading
          ? const LoadingScreen()
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 헤더
                  const Padding(
                    padding: EdgeInsets.only(bottom: 24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '동영상을 공유하세요',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        SizedBox(height: 8),
                        Text(
                          'AI가 요약하고 자동으로 정리해줍니다',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey,
                          ),
                        ),
                      ],
                    ),
                  ),

                  // URL 입력 필드
                  TextField(
                    controller: _urlController,
                    decoration: InputDecoration(
                      hintText: '동영상 링크를 붙여넣기 (YouTube 등)',
                      prefixIcon: const Icon(Icons.link),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      errorText: _errorMessage,
                    ),
                    onChanged: (_) {
                      setState(() => _errorMessage = null);
                    },
                  ),

                  const SizedBox(height: 24),

                  // 요약하기 버튼
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton.icon(
                      onPressed: _isLoading ? null : _summarize,
                      icon: const Icon(Icons.auto_awesome),
                      label: const Text('요약하기'),
                      style: ElevatedButton.styleFrom(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 32),

                  // 지원되는 플랫폼
                  const Text(
                    '지원되는 플랫폼',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      _PlatformChip('YouTube'),
                      _PlatformChip('Vimeo (준비 중)'),
                      _PlatformChip('Podcast (준비 중)'),
                    ],
                  ),

                  const SizedBox(height: 32),

                  // 특징
                  const Text(
                    '주요 기능',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const _FeatureItem(
                    icon: Icons.summarize,
                    title: 'AI 요약',
                    description: 'Claude AI로 동영상을 빠르게 요약합니다',
                  ),
                  const SizedBox(height: 12),
                  const _FeatureItem(
                    icon: Icons.insights,
                    title: '인사이트 추출',
                    description: '주식, AI, 학습 등 관심사 자동 분류',
                  ),
                  const SizedBox(height: 12),
                  const _FeatureItem(
                    icon: Icons.send,
                    title: '자동 배포',
                    description: 'Gmail, Obsidian, GitHub Pages 자동 저장',
                  ),
                ],
              ),
            ),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  Widget _buildBottomNav() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(
            color: Colors.grey.shade300,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _NavButton(
            icon: Icons.home,
            label: '홈',
            onPressed: () {},
          ),
          _NavButton(
            icon: Icons.history,
            label: '히스토리',
            onPressed: () {
              // TODO: 히스토리 화면으로 이동
            },
          ),
          _NavButton(
            icon: Icons.settings,
            label: '설정',
            onPressed: () {
              // TODO: 설정 화면으로 이동
            },
          ),
        ],
      ),
    );
  }
}

class _PlatformChip extends StatelessWidget {
  final String label;

  const _PlatformChip(this.label);

  @override
  Widget build(BuildContext context) {
    return Chip(
      label: Text(label),
      backgroundColor: Colors.blue.shade100,
      labelStyle: const TextStyle(color: Colors.blue),
    );
  }
}

class _FeatureItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;

  const _FeatureItem({
    required this.icon,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: Colors.blue, size: 24),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _NavButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  const _NavButton({
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onPressed,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: Colors.grey),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(fontSize: 12, color: Colors.grey),
          ),
        ],
      ),
    );
  }
}
