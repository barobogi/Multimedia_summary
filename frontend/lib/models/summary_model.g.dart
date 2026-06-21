// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'summary_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

VideoMetadata _$VideoMetadataFromJson(Map<String, dynamic> json) =>
    VideoMetadata(
      title: json['title'] as String,
      url: json['url'] as String,
      channel: json['channel'] as String?,
      description: json['description'] as String?,
      duration: (json['duration'] as num?)?.toInt(),
      publishDate: json['publishDate'] as String?,
      thumbnailUrl: json['thumbnailUrl'] as String?,
    );

Map<String, dynamic> _$VideoMetadataToJson(VideoMetadata instance) =>
    <String, dynamic>{
      'title': instance.title,
      'url': instance.url,
      'channel': instance.channel,
      'description': instance.description,
      'duration': instance.duration,
      'publishDate': instance.publishDate,
      'thumbnailUrl': instance.thumbnailUrl,
    };

SummaryResponse _$SummaryResponseFromJson(Map<String, dynamic> json) =>
    SummaryResponse(
      metadata:
          VideoMetadata.fromJson(json['metadata'] as Map<String, dynamic>),
      summary: json['summary'] as String,
      keyInsights: (json['keyInsights'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      categories: (json['categories'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      stockRelated: (json['stockRelated'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      aiRelated: (json['aiRelated'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      learningRelated: (json['learningRelated'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      timestamp: DateTime.parse(json['timestamp'] as String),
      processingTimeMs: (json['processingTimeMs'] as num).toDouble(),
    );

Map<String, dynamic> _$SummaryResponseToJson(SummaryResponse instance) =>
    <String, dynamic>{
      'metadata': instance.metadata,
      'summary': instance.summary,
      'keyInsights': instance.keyInsights,
      'categories': instance.categories,
      'stockRelated': instance.stockRelated,
      'aiRelated': instance.aiRelated,
      'learningRelated': instance.learningRelated,
      'timestamp': instance.timestamp.toIso8601String(),
      'processingTimeMs': instance.processingTimeMs,
    };

DistributionResult _$DistributionResultFromJson(Map<String, dynamic> json) =>
    DistributionResult(
      emailSent: json['emailSent'] as bool,
      obsidianSaved: json['obsidianSaved'] as bool,
      githubPagesUpdated: json['githubPagesUpdated'] as bool,
      errors:
          (json['errors'] as List<dynamic>).map((e) => e as String).toList(),
    );

Map<String, dynamic> _$DistributionResultToJson(DistributionResult instance) =>
    <String, dynamic>{
      'emailSent': instance.emailSent,
      'obsidianSaved': instance.obsidianSaved,
      'githubPagesUpdated': instance.githubPagesUpdated,
      'errors': instance.errors,
    };

FullResult _$FullResultFromJson(Map<String, dynamic> json) => FullResult(
      summary:
          SummaryResponse.fromJson(json['summary'] as Map<String, dynamic>),
      distribution: DistributionResult.fromJson(
          json['distribution'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$FullResultToJson(FullResult instance) =>
    <String, dynamic>{
      'summary': instance.summary,
      'distribution': instance.distribution,
    };
