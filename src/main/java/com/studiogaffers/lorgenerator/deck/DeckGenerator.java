package com.studiogaffers.lorgenerator.deck;


import com.studiogaffers.lorgenerator.LorgeneratorApplication;
import com.studiogaffers.lorgenerator.util.StreamGobbler;
import jnr.ffi.annotations.In;
import org.python.icu.util.Output;
import org.python.util.PythonInterpreter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.stereotype.Service;

import javax.annotation.Resources;
import java.io.*;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;
import java.util.Scanner;

@Service("deckGeneratorService")
public class DeckGenerator {

    static ResourceLoader resourceLoader;

    @Autowired
    public DeckGenerator(ResourceLoader resourceLoader) {
        this.resourceLoader = resourceLoader;
    }

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

            if(resourceLoader != null) {
                Resource resource = resourceLoader.getResource("classpath:deckCodes.txt");
                File f = resource.getFile();
                Scanner scanner = new Scanner(f);
                String res = scanner.nextLine();
                System.out.println(res);
                return res;
            } else {
                System.out.println("RESOURCE LOADER DOESNT EXIST");
                return "ERROR: CHECK CONSOLE";
            }

        } catch (Throwable t) {
            t.printStackTrace();
            return "ERROR: CHECK CONSOLE";
        }

    }

}
