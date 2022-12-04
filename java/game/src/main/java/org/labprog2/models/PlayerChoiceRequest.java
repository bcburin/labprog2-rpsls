package org.labprog2.models;

import java.util.List;

public class PlayerChoiceRequest {

    public int current_round;
    public int total_rounds;
    public List<String> past_winners;
    public List<PlayerChoiceInfo> player_choices;
    public List<String> options;
    public String player_name;
    public String game_id;
    public int match_number;


}
