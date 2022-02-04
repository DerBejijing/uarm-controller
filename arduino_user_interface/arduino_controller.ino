#define COMMAND_SUCCESS 0
#define ERROR_ARG_COUNT -1
#define ERROR_ARGS_INVALID -2

const String LED_LIST[] = {"R1", "G1"};
const int LEDS = 2;

String pinValues = "";

// yes, byte and bool are technically the same but
//  I cannot perform =! on bytes
//  which I have to
bool d_values[7];
byte a_values[3];


void setup() {
  Serial.begin(9600);
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  pinMode(6, INPUT_PULLUP);
  pinMode(7, INPUT_PULLUP);
  pinMode(8, INPUT_PULLUP);

  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);

  pinMode(A5, INPUT);
  pinMode(A4, INPUT);
  pinMode(A3, INPUT);

  processSignals();

  Serial.println("init");
}

void loop() {
  processCommands();
  processSignals();  

  delay(100);
}


void processSignals() {
  pinValues = "";
  
  processDigital(&pinValues);
  processAnalog(&pinValues);
  
  if(pinValues != "") {
    pinValues.remove(0, 1);
    Serial.println(pinValues);
  }  
}


void processCommands() {
  if(Serial.available()) {
    
    // read String until a newline
    String recieved = Serial.readStringUntil('\n');

    // get number of whitespaces in the recieved string
    // this is used to determine the number of arguments
    int argumentCount = getOccurenceCount(recieved, ' ');

    // the first substring of the recieved line is the command
    String command = getSplitString(recieved, ' ', 0);

    // create an array with the size being the number of arguments
    // this stores all arguments
    String arguments[argumentCount];

    // loop as many times as there are arguments to put them in the
    //  previously created argument array
    for(byte b = 1; b <= argumentCount; ++b) {
      arguments[b-1] = getSplitString(recieved, ' ', b);
    }

    // check for commands
    if(command == "S_L") Serial.println(commandLed(argumentCount, arguments));
  }  
}


int commandLed(int argumentCount, String arguments[]) {
  if(argumentCount == 2) {
    if(!(validLED(arguments[0]) && inRange(arguments[1].toInt(), 0, 1))) return ERROR_ARGS_INVALID;
        
      int pin = 0;
      if(arguments[0] == "G1") pin = 9;
      else if(arguments[0] == "R1") pin = 10;
      digitalWrite(pin, arguments[1].toInt());
        
      return COMMAND_SUCCESS;
  } else return ERROR_ARG_COUNT;
}


void processDigital(String* buf) {
  for(int i = 0; i < sizeof(d_values); ++i) {
    if(d_values[i] != digitalRead(i+2)) {
      d_values[i] =! d_values[i];
      *buf += "|";
      *buf += "D";
      *buf += i;
      *buf += ":";
      *buf += !d_values[i];
    }  
  }
}


void processAnalog(String* buf) {
  for(int i = 0; i < sizeof(a_values); ++i) {
    byte a_v = (byte) map(analogRead(i + 3), 0, 1023, 100, 0);
    byte delta = abs(a_values[i] - a_v);
    if(delta < 100 && delta > 1) {
      a_values[i] = a_v;
      *buf += "|";
      *buf += "A";
      *buf += i;
      *buf += ":";
      *buf += a_v;
    }
  }
}


// https://stackoverflow.com/questions/9072320/split-string-into-string-array
String getSplitString(String data, char separator, int index) {
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}


int getOccurenceCount(String data, char search) {
  int occurences = 0;
  for(char c : data) {
    if(c == search) ++occurences;
  }
  return occurences;
}


bool inRange(int i, int min, int max) {
  if(i >= min && i <= max) return true;
  return false;  
}

bool validLED(String led) {
  for(int i = 0; i < LEDS; ++i) {
    if(LED_LIST[i] == led) return true;  
  }
  return false;
}
