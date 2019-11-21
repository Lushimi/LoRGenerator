package com.studiogaffers.lorgenerator;

import no.stelar7.lor.LoRDeckCode;
import no.stelar7.lor.types.LoRCard;
import no.stelar7.lor.types.LoRDeck;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;

import java.util.Arrays;

@SpringBootApplication
public class LorgeneratorApplication {

    public static void main(String[] args) {
        SpringApplication.run(LorgeneratorApplication.class, args);
    }


}
