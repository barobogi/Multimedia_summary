import 'package:flutter/material.dart';
import 'package:multimedia_summary/screens/home_screen.dart';
import 'package:multimedia_summary/services/api_service.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(const MultimediaSummaryApp());
}

class MultimediaSummaryApp extends StatelessWidget {
  const MultimediaSummaryApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ApiService>(create: (_) => ApiService()),
      ],
      child: MaterialApp(
        title: 'Multimedia Summary',
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF3498DB),
            brightness: Brightness.light,
          ),
          typography: Typography.material2021(),
        ),
        darkTheme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF3498DB),
            brightness: Brightness.dark,
          ),
          typography: Typography.material2021(),
        ),
        home: const HomeScreen(),
      ),
    );
  }
}
