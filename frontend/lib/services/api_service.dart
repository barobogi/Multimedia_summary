import 'package:dio/dio.dart';
import 'package:logger/logger.dart';
import 'package:multimedia_summary/models/summary_model.dart';

class ApiService {
  late final Dio _dio;
  final Logger _logger = Logger();

  // API 기본 URL (환경에 따라 변경)
  // 개발: http://localhost:8000
  // 프로덕션: https://your-railway-app.up.railway.app
  static const String _baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'https://multimedia-summary.onrender.com',
  );

  static const Duration _connectTimeout = Duration(seconds: 30);
  static const Duration _receiveTimeout = Duration(seconds: 180);

  ApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: _baseUrl,
        connectTimeout: _connectTimeout,
        receiveTimeout: _receiveTimeout,
        contentType: 'application/json',
        responseType: ResponseType.json,
      ),
    );

    // 로깅 인터셉터 추가
    _dio.interceptors.add(
      LoggingInterceptor(_logger),
    );
  }

  /// 동영상 요약 요청 — YouTube는 서버에서 Gemini로 직접 처리
  Future<FullResult> summarizeVideo({
    required String videoUrl,
    String platform = 'youtube',
    String language = 'ko',
  }) async {
    try {
      _logger.i('Summarizing video: $videoUrl');

      final data = {
        'video_url': videoUrl,
        'platform': platform,
        'language': language,
      };

      final response = await _dio.post(
        '/api/summarize',
        data: data,
      );

      if (response.statusCode == 200) {
        final result = FullResult.fromJson(response.data);
        _logger.i('Summary generated successfully');
        return result;
      } else {
        throw Exception('Failed to summarize: ${response.statusCode}');
      }
    } on DioException catch (e) {
      _logger.e('DioException: ${e.message}');
      _handleDioError(e);
      rethrow;
    } catch (e) {
      _logger.e('Error: $e');
      rethrow;
    }
  }

  /// 헬스 체크
  Future<bool> healthCheck() async {
    try {
      final response = await _dio.get('/api/health');
      return response.statusCode == 200;
    } catch (e) {
      _logger.w('Health check failed: $e');
      return false;
    }
  }

  /// 준비 상태 확인
  Future<bool> readinessCheck() async {
    try {
      final response = await _dio.get('/api/health/ready');
      return response.statusCode == 200;
    } catch (e) {
      _logger.w('Readiness check failed: $e');
      return false;
    }
  }

  /// API URL 변경 (배포 후 사용)
  void setBaseUrl(String url) {
    _dio.options.baseUrl = url;
    _logger.i('Base URL changed to: $url');
  }

  /// Dio 에러 처리
  void _handleDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
        _logger.e('Connection timeout');
      case DioExceptionType.sendTimeout:
        _logger.e('Send timeout');
      case DioExceptionType.receiveTimeout:
        _logger.e('Receive timeout');
      case DioExceptionType.badResponse:
        _logger.e('Bad response: ${error.response?.statusCode}');
      case DioExceptionType.cancel:
        _logger.e('Request cancelled');
      case DioExceptionType.unknown:
        _logger.e('Unknown error: ${error.message}');
      case DioExceptionType.badCertificate:
        _logger.e('Bad certificate');
      case DioExceptionType.connectionError:
        _logger.e('Connection error: ${error.message}');
    }
  }
}

/// 로깅 인터셉터
class LoggingInterceptor extends Interceptor {
  final Logger _logger;

  LoggingInterceptor(this._logger);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    _logger.d('${options.method} ${options.path}');
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    _logger.d(
      '${response.statusCode} ${response.requestOptions.path}',
    );
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    _logger.e('Error: ${err.error}');
    handler.next(err);
  }
}
