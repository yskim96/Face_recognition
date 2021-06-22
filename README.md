# Face recognition
Body temperature Measured(AMG8833) and Face recognition(Azure Face API) on Raspberry Pi

# User Interface
![alt text](https://raw.githubusercontent.com/yskim96/Face_recognition/main/images/preview.gif "Preview User Interface")   
###### Face ID 아이콘 테두리 원형 도트 간 거리는 인식된 얼굴의 크기에 따라 상호작용하여 인식 품질을 항상시킬 수 있도록 유도합니다.  
###### 수 초 이상 얼굴이 인식되면 도트로 채워진 테두리의 두께가 두꺼워지고 이후 스틸 이미지를 생성합니다. 
  
  
  
  
외부요인으로 인해 안면 모니터링이 강제되는 경험이 은연중에 피로도를 쌓이게 하고 있다고 생각합니다.
기술을 통한 hospitality의 제공 가능성을 염두에 두고 사용자에게 영상 노출없이 애니메이션을 통한 상호작용을 유도하여 인식 절차에서 낮은 피로도를 기대하며 설계, 개발했습니다.


# Hardware

**Panasonic Grid-EYE® Infrared Array Sensors(AMG8833)**   
파나소닉에 의해 개발된 64화소의 온도 센서입니다. 8x8 배열의 센서가 방사체에서 방출되는 적외선을 측정합니다. Grid-EYE는 I2C 버스를 통해 통신하므로 Raspberry Pi 및 Arduino와 쉽게 호환됩니다. AMG8833에는 센서의 시야각을 60도로 제한하는 온 보드 렌즈가 포함되어있어 미드필드에 있는 물체를 감지하기에 적합합니다. 3.3V 및 5V에서 1Hz-10Hz의 샘플링 속도로 작동합니다. 0°C ~ 80°C 범위에서 온도를 측정 가능하며 대략적인 온도 분해능은 0.25°C입니다.

**5MP Night Vision Camera for Raspberry Pi(OV5647)**  
모든 버전의 Raspberry Pi와 호환되며 적외선 조명이 함께 제공됩니다. 적외선 야간 투시경 모드가 있으며 물체의 위치에 따라 초점링을 조정할 수 있습니다. 1W 고출력 850nm 적외선 조명을 사용하여 어두운 환경에서도 사용할 수 있습니다. 포토레지스터 및 가변저항은 주변 광원의 강도를 감지하고 적외선 조명 스위치의 임계값을 자동으로 조정합니다.

# To-Do
- AMG8833 온도 값 자동 보정 기능 
- 등록되지 않은 사용자 안면 조회시 QR등 추가 개인 신원인증 통하여 안면 값 매치  
- 등록된 사용자 출입시 안면인식 정확도에 따라 API 호출을 통하여 추가 학습  
- 안면 데이터와 체온 값을 매치하여 체온 로그 연동 


# Reference, Library
- https://kr.mouser.com/datasheet/2/315/panasonic_04262016_AMG88-1480161.pdf  
- https://makersportal.com/blog/thermal-camera-analysis-with-raspberry-pi-amg8833 
- https://www.dfrobot.com/product-1295.html 
- https://www.blog.pythonlibrary.org/2016/07/28/python-201-a-tutorial-on-threads/ 
- https://github.com/adafruit/Adafruit_CircuitPython_AMG88xx  
- https://github.com/Azure-Samples/cognitive-services-quickstart-code/tree/master/python/Face 
