import 'package:flutter/services.dart';

class ClipboardHelper {
  /// 클립보드에서 텍스트 가져오기
  static Future<String?> getClipboardText() async {
    try {
      final ClipboardData? data = await Clipboard.getData(Clipboard.kTextPlain);
      return data?.text;
    } catch (e) {
      return null;
    }
  }

  /// 텍스트를 클립보드에 복사
  static Future<void> copyToClipboard(String text) async {
    try {
      await Clipboard.setData(ClipboardData(text: text));
    } catch (e) {
      rethrow;
    }
  }
}
