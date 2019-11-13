package app.util;

import lombok.*;

public class Path {

    public static class Web {
        @Getter public static final String INDEX = "/index/";
    }

    public static class Template {
        public static final String INDEX = "/velocity/index/index.vm";
        public static final String NOT_FOUND = "/velocity/notFound.vm";
    }

}
