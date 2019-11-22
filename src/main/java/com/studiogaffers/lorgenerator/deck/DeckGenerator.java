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
        String[] commands = {"system.exe", "-get t"};
        System.out.println("Execing python process...");

        try {
            Process proc = rt.exec(path);

            BufferedReader stdInput = new BufferedReader(new 
            		InputStreamReader(proc.getInputStream()));
            
      
            java.util.Scanner s = new java.util.Scanner(stdInput).useDelimiter("\\A");
            
            String val = "";
            if (s.hasNext()) {
                val = s.next();
            }
            else {
                val = "";
            }
            val = val.replace("\n", "<br>");
            return val;
            
            //who even needs error messages
//            BufferedReader stdError = new BufferedReader(new 
//            	     InputStreamReader(proc.getErrorStream()));
//            
//            StringBuilder out = new StringBuilder();
//            
//            System.out.println("Here is the standard output of the command:\n");
//            String s = null;
//            while ((s = stdInput.readLine()) != null) {
//                System.out.println(s);
//            }
//
//            // Read any errors from the attempted command
//            System.out.println("Here is the standard error of the command (if any):\n");
//            while ((s = stdError.readLine()) != null) {
//                System.out.println(s);
//            }
//            
//            return out.toString();
//            System.out.println(out.toString());
            //screw error messages
            
            
            
//            // error msgs?
//            StreamGobbler errorGobbler = new StreamGobbler(proc.getErrorStream(), "ERROR");
//
//            // output msgs?
//            StreamGobbler outputGobbler = new StreamGobbler(proc.getInputStream(), "OUTPUT");
//
//            // get em
//            errorGobbler.start();
//            outputGobbler.start();
//
//            int exitVal = proc.waitFor();
//            System.out.println("ExitValue: " + exitVal);

//            if(resourceLoader != null) {
//                Resource resource = resourceLoader.getResource("classpath:deckCodes.txt");
            
            //my stuff
//                path = resource.getURI().toString();
//                File outfile = new File(path);
//                BufferedReader nbr = new BufferedReader(new FileReader(outfile));
//                String st;
//                while ((st = nbr.readLine()) != null)
//                	System.out.println(st);
//                System.out.println(resource.getURI());
//                return resource.getURI().toString();
            //my stuff end
            
//                InputStream is = resource.getInputStream();
//                BufferedReader br = new BufferedReader(new InputStreamReader(is));
//                StringBuilder out = new StringBuilder();
//                String line = br.readLine();
//                while ((line = br.readLine()) != null) {
//                    System.out.println(line);
//                    if(out.length() <= 0) out.append(line);
//                }
//                System.out.println(out.toString());
//                System.out.println("SOMETHING HAPPENED");
//                return out.toString();
//                
//            } else {
//                System.out.println("RESOURCE LOADER DOESNT EXIST");
//                return "ERROR: CHECK CONSOLE, resourceLoader == null";
//            }
            
        } catch (Throwable t) {
            t.printStackTrace();
            return "ERROR: CHECK CONSOLE, exception has occured";
        }

    }

}
