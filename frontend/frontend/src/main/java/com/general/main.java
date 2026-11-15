package com.general;
import javafx.application.Application;
import javafx.stage.Stage;
import javafx.fxml.*;
import javafx.scene.shape.Rectangle;
import javafx.*;
import javafx.scene.control.*;
import javafx.event.ActionEvent;
import javafx.scene.*;
import java.io.IOException;
import com.general.subjava.*;


public class main extends Application {
    @FXML
    private Label motivationSentence;

    @FXML
    private Rectangle first;

    @FXML
    private Label sportPoint;

    @FXML
    private Rectangle second;

    @FXML
    private Label dietPoit;

    @FXML
    private Rectangle third;

    @FXML
    private Label sleepPoint;

    @FXML
    private Button sportButton;

    @FXML
    private Button dietButton;

    @FXML
    private Button sleepButton;

    @FXML 
    private void onSeeAction(ActionEvent event) throws IOException {
        Button theButton = (Button) event.getSource();
        Parent root = null;

        if (theButton == sportButton) {
            root = FXMLLoader.load(getClass().getResource("/sport.fxml"));
        } else if (theButton == dietButton) {
            root = FXMLLoader.load(getClass().getResource("/meals.fxml"));
        } else if (theButton == sleepButton) {
           root = FXMLLoader.load(getClass().getResource("/sleepSchedule.fxml"));
        }

        Stage stage = (Stage) theButton.getScene().getWindow();
        stage.setScene(new Scene(root));
        stage.show();
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