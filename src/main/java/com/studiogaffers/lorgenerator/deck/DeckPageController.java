package com.studiogaffers.lorgenerator.deck;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;

@Controller
public class DeckPageController {

    @GetMapping("/deck")
    public String deckResults(Model model) {
        model.addAttribute("deck", new Deck("DECK"));
        return "deck";
    }

    @PostMapping("/deck")
    public String deckSubmit(@ModelAttribute Deck deck) {
        return "deck";
    }

}
