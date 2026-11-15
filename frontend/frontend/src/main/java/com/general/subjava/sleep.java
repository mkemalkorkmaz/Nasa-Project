package com.general.subjava;
import java.io.IOException;

import javafx.*;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.stage.Stage;
public class sleep extends Application{

    public static Parent createView() throws IOException {
        return FXMLLoader.load(sports.class.getResource("/sport.fxml"));
    }

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("Diet");
        primaryStage.show();
    }
    
    public static void main(String[] args) {
        launch(args);
    }
}
