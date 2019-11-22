package com.studiogaffers.lorgenerator.deck;


import org.python.util.PythonInterpreter;

import javax.annotation.Resource;
import javax.annotation.Resources;
import java.io.*;
import java.util.Scanner;

public class DeckGenerator {

    public static String generateDeck() {
        try {
            Process p = Runtime.getRuntime().exec("python python/main.py");
        } catch (Exception e) {
            System.out.println(e.getMessage());
            System.out.println(e.toString());
        }

        Scanner scanner = new Scanner(Resource)
    }

}
