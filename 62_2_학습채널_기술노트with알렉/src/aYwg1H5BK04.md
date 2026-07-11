---
video_id: aYwg1H5BK04
title: "파이썬 웹 크롤링 하기 - 너무 간단해서 민망합니다."
channel: "기술노트with 알렉"
date: 2020-06-24
category: "미분류"
priority: 99
views: 96,375
transcript: NO
generated: 2026-07-11 11:07
---

# 파이썬 웹 크롤링 하기 - 너무 간단해서 민망합니다.

**링크**: https://youtu.be/aYwg1H5BK04 | **날짜**: 2020-06-24 | **조회수**: 96,375 | **카테고리**: 미분류 | **우선순위**: 99

---

## 핵심 요약
[ AI 분석 대기 중 ]

## 주요 기술/도구
[ AI 분석 대기 중 ]

## 핵심 학습 내용
[ AI 분석 대기 중 ]

## 바로보기님 적용 포인트
[ AI 분석 대기 중 ]

## 신기술 발견
[ AI 분석 대기 중 ]

## 영상 설명란 원문
```
#파이썬#웹크롤링#크롤링#방법 간단하게 웹 사이트 크롤링하는 거 설명드려요~

소스입니다. 
from urllib.request import urlopen
from bs4 import BeautifulSoup

html = urlopen("https://news.naver.com/")

bsObject = BeautifulSoup(html, "html.parser")

#for link in bsObject.find_all('a'):
#    print(link.text.strip(), link.get('href'))

for link in bsObject.find_all('img'):
    print(link.text.strip(), link.get('src'))


안녕하세요. 기술노트 채널을 운영하고 있는 알렉이라고 합니다. 

IT분야에 개발자로 일을 하다가 프로젝트 매니저로 현재는 IT컨설턴트로 일하고 있습니다. 
IT전반에 걸친 경험이나 지식을 올리고 있습니다. 

개발...
```

## 자막 원문 (분석용)
*자막 없음 (not_found)*

---
*카드 생성: 2026-07-11 11:07 | 자막: not_found*
