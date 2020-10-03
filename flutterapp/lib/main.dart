import 'package:curved_navigation_bar/curved_navigation_bar.dart';
import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:zuko/pages/cameraPage.dart';
import 'package:zuko/pages/infoPage.dart';
import 'package:zuko/pages/mainPage.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:zuko/pages/mapPage.dart';
import 'package:zuko/screens/onboarding_screen.dart';

void main() => runApp(MyApp());

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}
class Data {
  double lat,long;
  Data({this.lat, this.long});
}
class _MyAppState extends State<MyApp> {
  String textValue = 'Hello World !';
  FirebaseMessaging firebaseMessaging = new FirebaseMessaging();
  FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin = new FlutterLocalNotificationsPlugin();
  double lat, long;

  void fcmSubscribe() {
    firebaseMessaging.subscribeToTopic('all');
  }

  @override
  void initState() {
    super.initState();
    fcmSubscribe();
    var android = new AndroidInitializationSettings('mipmap/ic_launcher');
    var ios = new IOSInitializationSettings();
    var platform = new InitializationSettings(android, ios);
    flutterLocalNotificationsPlugin.initialize(platform);

    final MapPage _mapPage = MapPage();

    firebaseMessaging.configure(
      onLaunch: (Map<String, dynamic> msg) {
          var data = msg['data'];
          lat = double.parse(data['lat']);
          long = double.parse(data['long']);
          Fluttertoast.showToast(
              msg: "Lat and long" + lat.toString() + " " + long.toString(),
              toastLength: Toast.LENGTH_SHORT,
              gravity: ToastGravity.CENTER,
              timeInSecForIos: 1,
              backgroundColor: Colors.red,
              textColor: Colors.white,
              fontSize: 16.0
          );
          _mapPage;
      },
      onResume: (Map<String, dynamic> msg) {
        var data = msg['data'];
        lat = data['lat'];
        long = data['long'];
        Fluttertoast.showToast(
            msg: "Lat and long" + lat.toString() + " " + long.toString(),
            toastLength: Toast.LENGTH_SHORT,
            gravity: ToastGravity.CENTER,
            timeInSecForIos: 1,
            backgroundColor: Colors.red,
            textColor: Colors.white,
            fontSize: 16.0
        );
        _mapPage;
      },
      onMessage: (Map<String, dynamic> msg) {
        showNotification(msg);
        var data = msg['data'];
          lat = data['lat'];
          long = data['long'];
        Fluttertoast.showToast(
            msg: "Lat and long" + lat.toString() + " " + long.toString(),
            toastLength: Toast.LENGTH_SHORT,
            gravity: ToastGravity.CENTER,
            timeInSecForIos: 1,
            backgroundColor: Colors.red,
            textColor: Colors.white,
            fontSize: 16.0
        );
        _mapPage;
      },
    );


    firebaseMessaging.requestNotificationPermissions(
        const IosNotificationSettings(sound: true, alert: true, badge: true));
    firebaseMessaging.onIosSettingsRegistered
        .listen((IosNotificationSettings setting) {
      print('IOS Setting Registed');
    });
    firebaseMessaging.getToken().then((token) {
      update(token);
    });
  }

  showNotification(Map<String, dynamic> msg) async {
    var android = new AndroidNotificationDetails(
      'sdffds dsffds',
      "CHANNLE NAME",
      "channelDescription",
    );
    var data = msg['notification'];
    String title = data['title'];
    String body = data['body'];

    var iOS = new IOSNotificationDetails();
    var platform = new NotificationDetails(android, iOS);
    await flutterLocalNotificationsPlugin.show(
        0, title, body, platform);
  }

  update(String token) {
    print(token);
    DatabaseReference databaseReference = new FirebaseDatabase().reference();
    databaseReference.child('fcm-token/${token}').set({"token": token});
    textValue = token;
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Volca',
      theme: ThemeData(
        brightness: Brightness.light,
        primaryColor: Colors.grey,
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
      ),
      home: MyHomePage(title: 'Volca'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _pageIndex = 2;

  FlutterTts flutterTts = new FlutterTts();
  Future speak(String txt) async {
    await flutterTts.setLanguage("en-US");
    await flutterTts.setPitch(1);
    await flutterTts.setSpeechRate(0.8);
    await flutterTts.speak(txt);
  }
  final CameraPage _cameraPage = CameraPage();
  final InfoPage _infoPage = InfoPage();
  final MainPage _mainPage = MainPage();
  final MapPage _mapPage = MapPage();
  final OnboardingScreen _safetyPage = OnboardingScreen();

  Widget _showPage = new MainPage();

  Widget _pageChooser(int page){
    switch(page) {
      case 0:
        speak("Before you leave, prepare your home");
        return _safetyPage;
        break;
      case 1:
        return _cameraPage;
        break;
      case 2:
        return _mainPage;
        break;
      case 3:
        return _infoPage;
        break;
      case 4:
        return _mapPage;
        break;
      default:
        return Container(
          child: new Center(
            child: new Text(
              'No page found',
              style: new TextStyle(fontSize: 30),
            ),
          )
        );
    }
  }



  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return Scaffold(
      bottomNavigationBar: CurvedNavigationBar(
        backgroundColor: Colors.black38,
        color: Colors.black45,
        buttonBackgroundColor: Colors.black54,
        index: _pageIndex,
        height: 50,
        animationDuration: Duration(milliseconds: 300),
        items: <Widget>[
          Icon(Icons.category, size: 30),
          Icon(Icons.camera_alt, size: 30),
          Icon(Icons.home, size: 30),
          Icon(Icons.person, size: 30),
          Icon(Icons.map, size: 30),
        ],
        onTap: (int tapped) {
          setState(() {
            _showPage = _pageChooser(tapped);
          });
        },
      ),
      body: Center(
        // Center is a layout widget. It takes a single child and positions it
        // in the middle of the parent.
        child: Center(
          child: _showPage,
        ),
      ), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}
