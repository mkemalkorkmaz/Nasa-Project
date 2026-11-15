package com.general.subjava;
import javafx.*;
import javafx.application.Application;
import javafx.stage.Stage;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.io.IOException;
import javafx.fxml.*;
import javafx.scene.Parent;
public class sports extends Application {

    public static Parent createView() throws IOException {
        return FXMLLoader.load(sports.class.getResource("/sport.fxml"));
    }

    public static String requestToPython(String json) throws IOException, InterruptedException {
        HttpClient client = HttpClient.newHttpClient();

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:5000/api/veri"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        System.out.println(response.statusCode() + " " + response.body());
        return response.body().toString();
    }

    @FXML

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("Diet");
        primaryStage.show();
    }
    
    public static void main(String[] args) throws IOException, InterruptedException{
        launch(args);
    }
}
//flask