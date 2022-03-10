#define error 5
#define wake 4
#define nonrem 3
#define rem 2

//ジャンパーされていると，LOWとなる  
#define jumperpin_w 8
#define jumperpin_n 7
#define jumperpin_r 6
#define ttl_outpin 10
#define observe_analogoutpin 9
#define clear_delay 100 //ms クリアするときにクリアするのを待つ時間
#define serialreadtimeout 15000 //about ms

//#define NELEMS(arg) (sizeof(arg) / sizeof((arg)[0]))
// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  delay(10);
  Serial.begin(9600);
  pinMode(error, OUTPUT);
  pinMode(wake, OUTPUT);
  pinMode(nonrem, OUTPUT);
  pinMode(rem, OUTPUT);
  pinMode(ttl_outpin, OUTPUT);
  pinMode(observe_analogoutpin, OUTPUT);
  delay(10);
  digitalWrite(error, LOW);
  digitalWrite(wake, LOW);
  digitalWrite(nonrem, LOW);
  digitalWrite(rem, LOW);

  TCCR1B &= B11111000;
  TCCR1B |= B00000001;// r=1の場合
}

byte byteval = (byte)0;
int val = 0;

void Analog_output(){
  if(val <= 255){
    analogWrite(observe_analogoutpin,val);
  }
  if(val >= 191){
    digitalWrite(rem, HIGH);
    digitalWrite(nonrem, LOW);
    digitalWrite(wake, LOW);
    digitalWrite(error, LOW);
  }else if(val >= 125){
    digitalWrite(rem, LOW);
    digitalWrite(nonrem, HIGH);
    digitalWrite(wake, LOW);
    digitalWrite(error, LOW);
  }else if(val >= 63){
    digitalWrite(rem, LOW);
    digitalWrite(nonrem, LOW);
    digitalWrite(wake, HIGH);
    digitalWrite(error, LOW);
  }else{
    digitalWrite(rem, LOW);
    digitalWrite(nonrem, LOW);
    digitalWrite(wake, LOW);
    digitalWrite(error, HIGH);
  }
}

// main roop
void loop() {
  if (Serial.available()) {
       byteval = Serial.read();
       val = (int)byteval;
       Analog_output();
  }
  delay(1); 
}
