import 'dart:developer';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:flutter/services.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:image_picker/image_picker.dart';
import 'package:location/location.dart';


class CameraPage extends StatefulWidget {
  @override
  _CameraPageState createState() => _CameraPageState();
}

class _CameraPageState extends State<CameraPage> {
  File _image;
  LocationData currentLocation;
  bool locationFlagError = false;

  static BaseOptions options = new BaseOptions(
  baseUrl: "http://192.168.8.236:6969",
  connectTimeout: 5000,
  receiveTimeout: 3000,
  );

  Dio dio = new Dio(options);

  Future uploadToServer() async {
    FormData formData= new FormData();

    if (currentLocation == null){
      formData = FormData.fromMap({
        "lat": "0",
        "long": "0",
        "file": await MultipartFile.fromFile(_image.path, filename: "image"),
      });
    }else{
      formData = FormData.fromMap({
        "lat": currentLocation.latitude.toString(),
        "long": currentLocation.longitude.toString(),
        "file": await MultipartFile.fromFile(_image.path, filename: "image"),
      });
    }

    var response = await dio.post("/detect", data: formData);
    log(response.toString());
  }

  Future getLatLong() async{
    var location = new Location();

// Platform messages may fail, so we use a try/catch PlatformException.
    try {
      currentLocation = await location.getLocation();
    } on PlatformException catch (e) {
      log(e.toString());
      if (e.code == 'PERMISSION_DENIED') {
        var error = 'Permission denied';
        Fluttertoast.showToast(
            msg: "Error:"+ error,
            toastLength: Toast.LENGTH_SHORT,
            gravity: ToastGravity.CENTER,
            timeInSecForIos: 1,
            backgroundColor: Colors.red,
            textColor: Colors.white,
            fontSize: 16.0
        );
      }
      currentLocation = null;
    }
  }

  Future getImage() async {
    var image = await ImagePicker.pickImage(source: ImageSource.camera);
    setState(() {
      _image = image;
    });
    getLatLong();
    uploadToServer();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        // Here we take the value from the MyHomePage object that was created by
        // the App.build method, and use it to set our appbar title.
        title: Text('Camera'),
      ),
      body: Center(
        child: _image == null
            ? Text('No image selected.')
            : Image.file(_image),


      ),
      floatingActionButton: FloatingActionButton(
        onPressed: getImage,
        tooltip: 'Pick Image',
        child: Icon(Icons.add_a_photo),
      ),
    );
  }

}