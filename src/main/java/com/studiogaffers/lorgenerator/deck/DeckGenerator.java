package com.studiogaffers.lorgenerator.deck;


import com.studiogaffers.lorgenerator.util.StreamGobbler;
import org.python.util.PythonInterpreter;

import javax.annotation.Resource;
import javax.annotation.Resources;
import java.io.*;
import java.util.Scanner;

public class DeckGenerator {

    public static String generateDeck() {
        String path = "python python/main.py";
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

        return "SUCCESS!!! CHECK CONSOLE";
    }

}
