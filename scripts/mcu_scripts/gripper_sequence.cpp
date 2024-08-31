#include <TimerTC3.h>
#include <string.h>

int closing_ms = 1000; // 1s
int data_interval_us = 10000; // 100 Hz
int rot_opn_val = 800;
bool g1_opn_flag = false;
bool g2_opn_flag = false;
bool curr_sens_initialized = false;
String sep = ",";
char request_pass;

int pwm_freq = 30000;
int duty = 0;

int RotSens1 = 0;
int RotSens2 = 2;
int PresSens1 = 1;
int PresSens2 = 3;
int CurrSens1 = 5;
int CurrSens2 = 6;

int MA_Phase = 9;
int MA_PWM = 10;
int MB_Phase = 7;
int MB_PWM = 8;

int RotSens1_data = 0;
int RotSens2_data = 0;
int PresSens1_data = 0;
int PresSens2_data = 0;
int CurrSens1_data = 0;
int CurrSens2_data = 0;
int CurrSensInit1_data = 0;
int CurrSensInit2_data = 0;

void initCurrSensor() {
  int zeroCurrVal1 = 0;
  int zeroCurrVal2 = 0;
  for (int i = 0; i < 200; i++){
    zeroCurrVal1 = zeroCurrVal1 + analogRead(CurrSens1);
    zeroCurrVal2 = zeroCurrVal2 + analogRead(CurrSens2);
  }
  CurrSensInit1_data = zeroCurrVal1 / 200;
  CurrSensInit2_data = zeroCurrVal2 / 200;
  curr_sens_initialized = true;
}

void sendSensorDataReq() {

  if (Serial.available() > 0){
    request_pass = Serial.read();

    if (request_pass == 'r'){
      int curr_val1 = 0;
      int curr_val2 = 0;
      for (int i = 0; i < 100; i++) {
        curr_val1 = curr_val1 + analogRead(CurrSens1);
        curr_val2 = curr_val2 + analogRead(CurrSens2);
      }
      RotSens1_data = analogRead(RotSens1);
      RotSens2_data = analogRead(RotSens2);
      PresSens1_data = analogRead(PresSens1);
      PresSens2_data = analogRead(PresSens2);
      // CurrSens1_data = analogRead(CurrSens1);
      // CurrSens2_data = analogRead(CurrSens2);
      CurrSens1_data = curr_val1/100;
      CurrSens2_data = curr_val2/100;

      Serial.println(RotSens1_data + sep + RotSens2_data + sep +
                    PresSens1_data + sep + PresSens2_data + sep +
                    CurrSens1_data + sep + CurrSens2_data + sep +
                    CurrSensInit1_data + sep + CurrSensInit2_data);
    }
  }
}

void sendSensorData() {
  int curr_val1 = 0;
  int curr_val2 = 0;
  for (int i = 0; i < 100; i++) {
    curr_val1 = curr_val1 + analogRead(CurrSens1);
    curr_val2 = curr_val2 + analogRead(CurrSens2);
  }
  RotSens1_data = analogRead(RotSens1);
  RotSens2_data = analogRead(RotSens2);
  PresSens1_data = analogRead(PresSens1);
  PresSens2_data = analogRead(PresSens2);
  // CurrSens1_data = analogRead(CurrSens1);
  // CurrSens2_data = analogRead(CurrSens2);
  CurrSens1_data = curr_val1/100;
  CurrSens2_data = curr_val2/100;

  Serial.println(RotSens1_data + sep + RotSens2_data + sep +
                PresSens1_data + sep + PresSens2_data + sep +
                CurrSens1_data + sep + CurrSens2_data + sep +
                CurrSensInit1_data + sep + CurrSensInit2_data);
}

void moveMotor(int motor, bool direction, int duty_cycle) {
  if (motor == 1){ // control motor 1
    if (direction) { // open grip
      digitalWrite(MA_Phase, LOW);
      pwm(MA_PWM, pwm_freq, duty_cycle);
    }
    else { // close grip
      digitalWrite(MA_Phase, HIGH);
      pwm(MA_PWM, pwm_freq, duty_cycle);
    }
  } else if (motor == 2){ // control motor 2
    if (direction) { // open grip
      digitalWrite(MB_Phase, LOW);
      pwm(MB_PWM, pwm_freq, duty_cycle);
    }
    else { // close grip
      digitalWrite(MB_Phase, HIGH);
      pwm(MB_PWM, pwm_freq, duty_cycle);
    }
  }
}

void stopMotor(int motor) {
  if (motor == 1){ // stop motor 1
    pwm(MA_PWM, pwm_freq, 0);
  } else if (motor == 2){ // stop motor 2
    pwm(MB_PWM, pwm_freq, 0);
  }
}

void openGrip(int duty_cycle) {
  if (RotSens1_data < rot_opn_val){
    moveMotor(1, true, duty_cycle);
  } else {
    stopMotor(1);
    g1_opn_flag = true;
  }
  if (RotSens2_data < rot_opn_val){
    moveMotor(2, true, duty_cycle);
  } else {
    stopMotor(2);
    g2_opn_flag = true;
  }
}

void closeGrip(int duty_cycle) {
  moveMotor(1, false, duty_cycle);
  moveMotor(2, false, duty_cycle);
  
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(RotSens1, INPUT);
  pinMode(RotSens2, INPUT);
  pinMode(PresSens1, INPUT);
  pinMode(PresSens2, INPUT);
  pinMode(CurrSens1, INPUT);
  pinMode(CurrSens2, INPUT);

  pinMode(MA_Phase, OUTPUT);
  pinMode(MA_PWM, OUTPUT);
  pinMode(MB_Phase, OUTPUT);
  pinMode(MB_PWM, OUTPUT);

  TimerTc3.initialize(data_interval_us);
  TimerTc3.attachInterrupt(sendSensorData);

  initCurrSensor();
}

void loop() {
  // put your main code here, to run repeatedly:
  openGrip(1024/2); //open grip with half speed
  if (g1_opn_flag == true && g2_opn_flag == true) {
    g1_opn_flag = false;
    g2_opn_flag = false;
    for (duty = 0; duty <= 1024; duty++) {
      closeGrip(duty);
      delay(10);
    }
    delay(closing_ms);
  }
}
