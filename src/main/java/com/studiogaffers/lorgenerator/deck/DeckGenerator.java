package com.studiogaffers.lorgenerator.deck;


import org.python.util.PythonInterpreter;

import java.io.*;

public class DeckGenerator {

    public static String generateDeck() throws IOException {
        Process p = Runtime.getRuntime().exec("python python/main.py");
        System.out.println(p.isAlive());
        BufferedReader stdInput = new BufferedReader(new InputStreamReader(p.getInputStream()));
        System.out.println(stdInput.readLine());

        return stdInput.readLine();
    }

}
