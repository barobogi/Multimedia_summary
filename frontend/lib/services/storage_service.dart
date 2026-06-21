import 'package:shared_preferences/shared_preferences.dart';
import 'package:multimedia_summary/models/summary_model.dart';
import 'dart:convert';
import 'package:logger/logger.dart';

class StorageService {
  static const String _summaryHistoryKey = 'summary_history';
  static const String _apiBaseUrlKey = 'api_base_url';
  static const int _maxHistoryItems = 100;

  final Logger _logger = Logger();
  late final SharedPreferences _prefs;

  /// 초기화
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    _logger.i('StorageService initialized');
  }

  /// 요약 히스토리 저장
  Future<void> saveSummary(FullResult result) async {
    try {
      final history = await getSummaryHistory();

      // 새 항목 추가
      history.insert(0, result);

      // 최대 개수 제한
      if (history.length > _maxHistoryItems) {
        history.removeRange(_maxHistoryItems, history.length);
      }

      // JSON 인코딩
      final jsonList = history
          .map((item) => jsonEncode(item.toJson()))
          .toList();

      await _prefs.setStringList(_summaryHistoryKey, jsonList);
      _logger.i('Saved summary: ${result.summary.metadata.title}');
    } catch (e) {
      _logger.e('Error saving summary: $e');
    }
  }

  /// 요약 히스토리 조회
  Future<List<FullResult>> getSummaryHistory() async {
    try {
      final jsonList = _prefs.getStringList(_summaryHistoryKey) ?? [];

      return jsonList
          .map((json) => FullResult.fromJson(jsonDecode(json)))
          .toList();
    } catch (e) {
      _logger.e('Error loading summary history: $e');
      return [];
    }
  }

  /// 특정 요약 조회
  Future<FullResult?> getSummary(int index) async {
    try {
      final history = await getSummaryHistory();
      if (index >= 0 && index < history.length) {
        return history[index];
      }
      return null;
    } catch (e) {
      _logger.e('Error getting summary: $e');
      return null;
    }
  }

  /// 요약 삭제
  Future<void> deleteSummary(int index) async {
    try {
      final history = await getSummaryHistory();
      if (index >= 0 && index < history.length) {
        history.removeAt(index);

        final jsonList = history
            .map((item) => jsonEncode(item.toJson()))
            .toList();

        await _prefs.setStringList(_summaryHistoryKey, jsonList);
        _logger.i('Deleted summary at index: $index');
      }
    } catch (e) {
      _logger.e('Error deleting summary: $e');
    }
  }

  /// 히스토리 전체 삭제
  Future<void> clearHistory() async {
    try {
      await _prefs.remove(_summaryHistoryKey);
      _logger.i('History cleared');
    } catch (e) {
      _logger.e('Error clearing history: $e');
    }
  }

  /// API Base URL 저장
  Future<void> setApiBaseUrl(String url) async {
    try {
      await _prefs.setString(_apiBaseUrlKey, url);
      _logger.i('API Base URL saved: $url');
    } catch (e) {
      _logger.e('Error saving API URL: $e');
    }
  }

  /// API Base URL 조회
  String getApiBaseUrl() {
    return _prefs.getString(_apiBaseUrlKey) ?? 'http://localhost:8000';
  }

  /// 캐시 크기 조회
  Future<int> getCacheSize() async {
    try {
      final history = await getSummaryHistory();
      return history.length;
    } catch (e) {
      _logger.e('Error getting cache size: $e');
      return 0;
    }
  }

  /// 캐시 통계
  Future<Map<String, dynamic>> getCacheStats() async {
    try {
      final history = await getSummaryHistory();
      final categories = <String, int>{};
      final platforms = <String, int>{};

      for (final item in history) {
        for (final cat in item.summary.categories) {
          categories[cat] = (categories[cat] ?? 0) + 1;
        }
      }

      return {
        'total_items': history.length,
        'categories': categories,
        'oldest_item': history.isNotEmpty
            ? history.last.summary.timestamp
            : null,
        'newest_item': history.isNotEmpty
            ? history.first.summary.timestamp
            : null,
      };
    } catch (e) {
      _logger.e('Error getting cache stats: $e');
      return {};
    }
  }
}
