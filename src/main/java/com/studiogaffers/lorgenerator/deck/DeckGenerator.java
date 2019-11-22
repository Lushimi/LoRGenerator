package com.studiogaffers.lorgenerator.deck;


import com.studiogaffers.lorgenerator.LorgeneratorApplication;
import com.studiogaffers.lorgenerator.util.StreamGobbler;
import jnr.ffi.annotations.In;
import org.python.apache.commons.compress.utils.IOUtils;
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
import java.nio.Buffer;
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
                Resource resource = resourceLoader.getResource("deckCodes.txt");
                System.out.println(resource.getURI());
                System.out.println("testing");
                InputStream is = resource.getInputStream();
                BufferedReader br = new BufferedReader(new InputStreamReader(is));
                StringBuilder out = new StringBuilder();
                String line;
                while ((line = br.readLine()) != null) {
                    System.out.println(line);
                    if(out.length() <= 0) out.append(line);
                }
                System.out.println(out.toString());
                System.out.println("SOMETHING HAPPENED");

                return out.toString();
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
