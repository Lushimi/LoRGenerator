package com.studiogaffers.lorgenerator.index;

import com.studiogaffers.lorgenerator.deck.Deck;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;

@Controller
public class IndexController {

    @GetMapping("/")
    public String index(Model model) {
        Deck d = new Deck();
        d.setDeckCode("TEST");
        model.addAttribute("deck", d);
        return "index";
    }

    @PostMapping("/index")
    public String indexSubmit(@ModelAttribute Deck deck) {
        return "deck";
    }

}
