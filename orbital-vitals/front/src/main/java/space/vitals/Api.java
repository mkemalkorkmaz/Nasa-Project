package space.vitals;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse.BodyHandlers;

/** Thin HTTP client for the Python backend. */
final class Api {
    private final HttpClient http = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(java.time.Duration.ofSeconds(3)).build();
    private final String base;

    Api(String base) { this.base = base; }

    byte[] frame() throws Exception {
        return http.send(HttpRequest.newBuilder(URI.create(base + "/frame.jpg")).build(), BodyHandlers.ofByteArray()).body();
    }

    JsonObject state() throws Exception {
        var res = http.send(HttpRequest.newBuilder(URI.create(base + "/api/state")).build(), BodyHandlers.ofString());
        if (res.statusCode() != 200) throw new RuntimeException("HTTP " + res.statusCode() + ": " + res.body());
        return JsonParser.parseString(res.body()).getAsJsonObject();
    }

    void post(String path, String json) {
        try {
            http.send(HttpRequest.newBuilder(URI.create(base + path))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(json)).build(), BodyHandlers.discarding());
        } catch (Exception ignored) { }
    }
}
