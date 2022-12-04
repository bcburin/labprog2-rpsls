package org.labprog2.models;

public class PlayerChoiceResponse {
    public String shape;
    public String player_name;
    public String game_id;
    public int match_number;


    public PlayerChoiceResponse(String player_name, String game_id, int match_number, String shape) {
        this.shape = shape;
        this.player_name = player_name;
        this.game_id = game_id;
        this.match_number = match_number;
    }
}
