package computerdatabase;
import java.time.Duration;

import static io.gatling.javaapi.core.CoreDsl.*;
import static io.gatling.javaapi.http.HttpDsl.*;

import io.gatling.javaapi.core.*;
import io.gatling.javaapi.http.*;

public class ComputerDatabaseSimulation extends Simulation {
    HttpProtocolBuilder httpProtocol =
        http.baseUrl("http://127.0.0.1:8080")
        .acceptHeader("text/html");

ScenarioBuilder myScenario = scenario("My Scenario")
    .exec(
        repeat(120).on(                // Repeat the following block for 120 iterations
            exec(
                http("Req").get("/cpu")  // Request to "/cpu"
            ).pause(10)                 // Pause for 10 seconds between requests
        )
    );
    {
       setUp(
    myScenario.injectOpen(
        rampUsers(200).during(10),      // Ramp 200 users over 10 seconds
        nothingFor(10),                 // Pause for 10 seconds
        atOnceUsers(100)                // Instantly inject 100 users
    )
).protocols(httpProtocol)
 .maxDuration(Duration.ofMinutes(20));
    }}