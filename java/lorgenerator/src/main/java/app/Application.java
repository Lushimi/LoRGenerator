package app;

import app.index.IndexController;
import app.util.Filters;
import app.util.Path;

import static spark.Spark.*;
import static spark.debug.DebugScreen.*;

public class Application {

    public static void main(String[] args) {
        port(4567);
        staticFiles.location("/public");
        enableDebugScreen();

        before("*", Filters.addTrailingSlashes);

        get(Path.Web.INDEX, IndexController.serveIndexPage);
    }
}
