import 'package:json_annotation/json_annotation.dart';

part 'summary_model.g.dart';

@JsonSerializable()
class VideoMetadata {
  final String title;
  final String url;
  final String? channel;
  final String? description;
  final int? duration;
  final String? publishDate;
  final String? thumbnailUrl;

  VideoMetadata({
    required this.title,
    required this.url,
    this.channel,
    this.description,
    this.duration,
    this.publishDate,
    this.thumbnailUrl,
  });

  factory VideoMetadata.fromJson(Map<String, dynamic> json) =>
      _$VideoMetadataFromJson(json);

  Map<String, dynamic> toJson() => _$VideoMetadataToJson(this);
}

@JsonSerializable()
class SummaryResponse {
  final VideoMetadata metadata;
  final String summary;
  final List<String> keyInsights;
  final List<String> categories;
  final List<String>? stockRelated;
  final List<String>? aiRelated;
  final List<String>? learningRelated;
  final DateTime timestamp;
  final double processingTimeMs;

  SummaryResponse({
    required this.metadata,
    required this.summary,
    required this.keyInsights,
    required this.categories,
    this.stockRelated,
    this.aiRelated,
    this.learningRelated,
    required this.timestamp,
    required this.processingTimeMs,
  });

  factory SummaryResponse.fromJson(Map<String, dynamic> json) =>
      _$SummaryResponseFromJson(json);

  Map<String, dynamic> toJson() => _$SummaryResponseToJson(this);
}

@JsonSerializable()
class DistributionResult {
  final bool emailSent;
  final bool obsidianSaved;
  final bool githubPagesUpdated;
  final List<String> errors;

  DistributionResult({
    required this.emailSent,
    required this.obsidianSaved,
    required this.githubPagesUpdated,
    required this.errors,
  });

  factory DistributionResult.fromJson(Map<String, dynamic> json) =>
      _$DistributionResultFromJson(json);

  Map<String, dynamic> toJson() => _$DistributionResultToJson(this);
}

@JsonSerializable()
class FullResult {
  final SummaryResponse summary;
  final DistributionResult distribution;

  FullResult({
    required this.summary,
    required this.distribution,
  });

  factory FullResult.fromJson(Map<String, dynamic> json) =>
      _$FullResultFromJson(json);

  Map<String, dynamic> toJson() => _$FullResultToJson(this);
}
