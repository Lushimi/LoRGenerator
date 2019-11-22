package com.studiogaffers.lorgenerator.deck;


import com.studiogaffers.lorgenerator.LorgeneratorApplication;
import com.studiogaffers.lorgenerator.util.StreamGobbler;
import jnr.ffi.annotations.In;
import org.python.util.PythonInterpreter;

import javax.annotation.Resource;
import javax.annotation.Resources;
import java.io.*;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;
import java.util.Scanner;

public class DeckGenerator {

    public static String generateDeck() {
        String path = "python python/DeckAlgo.py";
        Runtime rt = Runtime.getRuntime();
        System.out.println("Execing python process...");

        try {
            Process proc = rt.exec(path);

            // error msgs?
            StreamGobbler errorGobbler = new StreamGobbler(proc.getErrorStream(), "ERROR");

            // output msgs?
            StreamGobbler outputGobbler = new StreamGobbler(proc.getInputStream(), "OUTPUT");

            // get em
            errorGobbler.start();
            outputGobbler.start();

            int exitVal = proc.waitFor();
            System.out.println("ExitValue: " + exitVal);

        } catch (Throwable t) {
            t.printStackTrace();
            return "ERROR: CHECK CONSOLE";
        }


        try {
            Class cls = Class.forName("com.studiogaffers.lorgenerator.LorgeneratorApplication");
            ClassLoader classLoader = cls.getClassLoader();
            InputStream i = classLoader.getResourceAsStream("deckCodes.txt");
            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(i));
            String res = bufferedReader.readLine();
            i.close();
            System.out.println(res);
            return res;

        } catch (Throwable t) {
            t.printStackTrace();
            return "ERROR: SEE CONSOLE";
        }

    }

}
