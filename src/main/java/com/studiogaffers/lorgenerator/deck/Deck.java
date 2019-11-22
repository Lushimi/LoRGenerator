package com.studiogaffers.lorgenerator.deck;

import lombok.Data;
import lombok.Getter;
import lombok.Setter;
import lombok.Value;

public class Deck {

    private String deckCode;

    public Deck() {
        this.deckCode = "";
    }

    public Deck(String code) {
        this.deckCode = code;
    }

    public void setDeckCode(String code) {
        this.deckCode = code;
    }

    public String getDeckCode() {
        return deckCode;
    }

    public String generateRandomDeck() {
        deckCode = DeckGenerator.generateDeck();
        return deckCode;
    }
}
