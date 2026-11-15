package space.vitals;

import com.google.gson.JsonObject;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.scene.control.Button;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressBar;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.*;
import javafx.stage.Stage;

import java.io.ByteArrayInputStream;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class App extends Application {
    private final Api api = new Api(System.getenv().getOrDefault("VITALS_API", "http://127.0.0.1:8000"));
    private final ScheduledExecutorService pool = Executors.newScheduledThreadPool(3, r -> {
        Thread t = new Thread(r); t.setDaemon(true); return t;
    });

    private final ImageView video = new ImageView();
    private final Label conn = label("● connecting", "small");
    private final Label sleepState = label("—", "big"), sleepTime = label("", "small"), sleepMeta = label("", "small");
    private final ProgressBar sleepQuality = new ProgressBar(0);
    private final Label reps = label("0", "big"), workoutMeta = label("", "small");
    private final Label water = label("0 ml", "big"), food = label("0 kcal", "big"), intakeMeta = label("", "small");
    private final ProgressBar waterBar = new ProgressBar(0), foodBar = new ProgressBar(0);
    private final XYChart.Series<Number, Number> motion = new XYChart.Series<>();
    private int tick;

    @Override
    public void start(Stage stage) {
        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);
        HBox header = new HBox(12, new VBox(2, label("ORBITAL VITALS", "title"),
                label("Crew health monitor · powered by MediaPipe", "small")), spacer, conn);
        header.setAlignment(Pos.CENTER_LEFT);

        // live camera
        video.setPreserveRatio(true);
        StackPane videoBox = new StackPane(video);
        videoBox.getStyleClass().add("card");
        videoBox.setMinSize(0, 0);
        video.fitWidthProperty().bind(videoBox.widthProperty().subtract(32));
        HBox.setHgrow(videoBox, Priority.ALWAYS);

        // sleep
        sleepQuality.setMaxWidth(Double.MAX_VALUE);
        VBox sleep = card("SLEEP", sleepState, sleepTime, sleepMeta, label("Sleep quality", "small"), sleepQuality);

        // workout
        ChoiceBox<String> exercise = new ChoiceBox<>();
        exercise.getItems().addAll("squat", "pushup", "curl");
        exercise.setValue("squat");
        exercise.setOnAction(e -> pool.execute(() -> api.post("/api/exercise", "{\"name\":\"" + exercise.getValue() + "\"}")));
        HBox repRow = new HBox(14, reps, label("reps", "small"), exercise);
        repRow.setAlignment(Pos.CENTER_LEFT);
        VBox workout = card("WORKOUT", repRow, workoutMeta);

        // consumption
        waterBar.setMaxWidth(Double.MAX_VALUE);
        foodBar.setMaxWidth(Double.MAX_VALUE);
        Button addWater = button("+250 ml water", false), addFood = button("+600 kcal meal", false), reset = button("Reset", true);
        addWater.setOnAction(e -> pool.execute(() -> api.post("/api/intake", "{\"kind\":\"water\",\"amount\":250}")));
        addFood.setOnAction(e -> pool.execute(() -> api.post("/api/intake", "{\"kind\":\"food\",\"amount\":600}")));
        reset.setOnAction(e -> pool.execute(() -> api.post("/api/reset", "{}")));
        HBox bars = new HBox(20, new VBox(4, water, waterBar), new VBox(4, food, foodBar));
        bars.getChildren().forEach(n -> HBox.setHgrow(n, Priority.ALWAYS));
        VBox cons = card("CONSUMPTION", bars, intakeMeta, new FlowPane(8, 8, addWater, addFood, reset));

        // movement chart
        NumberAxis x = new NumberAxis(), y = new NumberAxis();
        x.setTickLabelsVisible(false); x.setTickMarkVisible(false); x.setForceZeroInRange(false);
        LineChart<Number, Number> chart = new LineChart<>(x, y);
        chart.setCreateSymbols(false); chart.setLegendVisible(false); chart.setAnimated(false);
        chart.setPrefHeight(140); chart.getData().add(motion);
        VBox movement = card("MOVEMENT LEVEL", chart);

        VBox right = new VBox(12, sleep, workout, cons, movement);
        right.setPrefWidth(380); right.setMinWidth(380);

        BorderPane root = new BorderPane();
        root.setPadding(new Insets(20));
        root.setTop(header);
        HBox center = new HBox(16, videoBox, right);
        BorderPane.setMargin(center, new Insets(16, 0, 0, 0));
        root.setCenter(center);

        Scene scene = new Scene(root, 1240, 800);
        scene.getStylesheets().add(getClass().getResource("/styles.css").toExternalForm());
        stage.setTitle("Orbital Vitals");
        stage.setScene(scene);
        stage.show();

        pool.scheduleWithFixedDelay(this::pollFrame, 0, 80, TimeUnit.MILLISECONDS);
        pool.scheduleWithFixedDelay(this::pollState, 0, 500, TimeUnit.MILLISECONDS);
    }

    private void pollFrame() {
        try {
            byte[] b = api.frame();
            if (b.length > 0) {
                Image img = new Image(new ByteArrayInputStream(b));
                if (!img.isError()) Platform.runLater(() -> video.setImage(img));
            }
        } catch (Exception ignored) { }
    }

    private void pollState() {
        try {
            JsonObject s = api.state();
            Platform.runLater(() -> render(s));
        } catch (Exception e) {
            e.printStackTrace();
            String msg = String.valueOf(e);
            Platform.runLater(() -> { conn.setText("● offline: " + msg.substring(0, Math.min(70, msg.length()))); conn.setStyle("-fx-text-fill:#ff6b6b;"); });
        }
    }

    private void render(JsonObject s) {
        conn.setText("● live"); conn.setStyle("-fx-text-fill:#3ddc97;");
        JsonObject sl = s.getAsJsonObject("sleep"), wo = s.getAsJsonObject("workout"), co = s.getAsJsonObject("consumption");

        sleepState.setText(sl.get("sleeping").getAsBoolean() ? "Sleeping" : "Awake");
        sleepTime.setText("Time asleep: " + hms(sl.get("total_s").getAsDouble()));
        String ear = sl.get("ear").isJsonNull() ? "n/a" : String.format("%.2f", sl.get("ear").getAsDouble());
        sleepMeta.setText(String.format("Posture: %s · Movements: %d · Eye ratio: %s",
                s.get("posture").getAsString(), sl.get("movements").getAsInt(), ear));
        sleepQuality.setProgress(sl.get("quality").getAsInt() / 100.0);

        reps.setText(String.valueOf(wo.get("reps").getAsInt()));
        workoutMeta.setText(String.format("%s · %.1f kcal burned · %d total reps",
                wo.get("exercise").getAsString(), wo.get("kcal").getAsDouble(), wo.get("total_reps").getAsInt()));

        int w = co.get("water_ml").getAsInt(), f = co.get("food_kcal").getAsInt();
        water.setText(w + " ml"); food.setText(f + " kcal");
        waterBar.setProgress(Math.min(1, w / co.get("water_goal").getAsDouble()));
        foodBar.setProgress(Math.min(1, f / co.get("food_goal").getAsDouble()));
        intakeMeta.setText("Goals: " + co.get("water_goal").getAsInt() + " ml · " + co.get("food_goal").getAsInt()
                + " kcal · Detected bites/sips: " + co.get("detected_intakes").getAsInt());

        motion.getData().add(new XYChart.Data<>(tick++, s.get("motion").getAsDouble() * 100));
        if (motion.getData().size() > 60) motion.getData().remove(0);
    }

    private static String hms(double sec) {
        long t = (long) sec;
        return String.format("%02d:%02d:%02d", t / 3600, (t % 3600) / 60, t % 60);
    }

    private static Label label(String text, String style) {
        Label l = new Label(text); l.getStyleClass().add(style); return l;
    }

    private static VBox card(String title, Node... children) {
        VBox box = new VBox(8, label(title, "card-title"));
        box.getChildren().addAll(children);
        box.getStyleClass().add("card");
        return box;
    }

    private static Button button(String text, boolean ghost) {
        Button b = new Button(text);
        if (ghost) b.getStyleClass().add("ghost");
        return b;
    }

    public static void main(String[] args) { launch(args); }
}
