package app;

import app.util.Filters;

import static spark.Spark.*;

public class Application {

    public static void main(String[] args) {
        port(4567);
        staticFiles.location("/public");

        before("*", Filters.addTrailingSlashes);
    }
}
