/**
 * This code is from https://www.javaworld.com/article/2071275/when-runtime-exec---won-t.html
 */
package com.studiogaffers.lorgenerator.util;

import java.util.*;
import java.io.*;
public class StreamGobbler extends Thread{

    private InputStream is;
    private String type;

    public StreamGobbler(InputStream is, String type) {
        this.is = is;
        this.type = type;
    }

    public void run() {
        try {
            InputStreamReader isr = new InputStreamReader(is);
            BufferedReader br = new BufferedReader(isr);
            String line = null;
            while ((line = br.readLine()) != null) {
                System.out.println(type + ">" + line);
            }
        } catch (IOException ioe) {
            ioe.printStackTrace();
        }
    }

}
