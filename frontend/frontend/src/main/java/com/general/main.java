package com.general;

import com.general.subjava.diet;
import com.general.subjava.sleep;
import com.general.subjava.sports;
import java.io.IOException;
import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.shape.Rectangle;
import javafx.stage.Stage;

public class main extends Application {

    @FXML private Label motivationSentence;
    @FXML private Rectangle first;
    @FXML private Label sportPoint;
    @FXML private Rectangle second;
    @FXML private Label dietPoint;   // FXML'deki fx:id ile birebir aynı olmalı
    @FXML private Rectangle third;
    @FXML private Label sleepPoint;
    @FXML private Button sportButton;
    @FXML private Button dietButton;
    @FXML private Button sleepButton;

    @FXML
    void onSeeAction(ActionEvent event) throws IOException {
        Button theButton = (Button) event.getSource();
        Parent root;

        if (theButton == sportButton) {
            root = sports.createView();
        } else if (theButton == dietButton) {
            root = diet.createView();
        } else if (theButton == sleepButton) {
            root = sleep.createView();
        } else {
            return;
        }

        Stage stage = (Stage) theButton.getScene().getWindow();
        stage.setScene(new Scene(root));
    }

    @Override
    public void start(Stage primaryStage) throws Exception {
        FXMLLoader loader = new FXMLLoader(getClass().getResource("/main.fxml"));
        Parent root = loader.load();
        primaryStage.setTitle("Take Care");
        primaryStage.setScene(new Scene(root));
        primaryStage.show();
    }

    public static void main(String[] args) {
        Application.launch(args);
    }
}
