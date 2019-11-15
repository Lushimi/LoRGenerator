package app.index;

import app.util.*;
import spark.*;
import java.util.*;
import static app.Application.*;
import org.python.util.PythonInterpreter;
import javax.script.ScriptContext;
import javax.script.SimpleScriptContext;

public class IndexController {

    public static Route serveIndexPage = (Request request, Response response) -> {
        Map<String, Object> model = new HashMap<>();
        return ViewUtil.render(request, model, Path.Template.INDEX);
    };

}
