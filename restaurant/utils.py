
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 문장에서 명사를 추출하는 형태소 분석 라이브러리
import jpype
from konlpy.tag import Hannanum
import io, os
import base64


def make_wordcloud(reviews_text, font_path):
  if not reviews_text.strip():  
      return None
  else:
      # 형태소 분석을 통해 명사 추출
      hannanum = Hannanum()
      nouns = hannanum.nouns(reviews_text)
      words = [noun for noun in nouns if len(noun) > 1]
      
      # WordCloud 생성
      wordcloud = WordCloud(
          font_path= font_path,
          background_color='white',
          width=500,
          height=500
      ).generate(words)  # 텍스트(빈도 1 초과인 명사)로부터 단어 클라우드 생성

      # 이미지로 저장
      fig, ax = plt.subplots(figsize=(5, 5))
      ax.imshow(wordcloud, interpolation='bilinear')
      ax.axis('off')  # 축을 숨김
      buf = io.BytesIO()
      plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
      plt.close(fig)
      buf.seek(0)
      image_base64 = base64.b64encode(buf.read()).decode('utf-8')

      return image_base64
