package org.labprog2.models;

import java.util.List;

public class EndOfGameMessage {
    public String winner;
    public int current_round;
    public int total_rounds;
    public List<String> past_winners;
    public List<PlayerChoiceInfo> player_choices;
}
