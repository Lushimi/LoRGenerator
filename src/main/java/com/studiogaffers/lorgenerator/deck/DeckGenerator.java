package com.studiogaffers.lorgenerator.deck;


import org.python.util.PythonInterpreter;

import java.io.*;

public class DeckGenerator {

    public static String generateDeck() {
        try {
            Process p = Runtime.getRuntime().exec("python python/main.py");
        } catch (Exception e) {
            System.out.println(e.getMessage());
            System.out.println(e.toString());
        }

    }

}
