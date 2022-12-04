package org.labprog2.client;

import org.labprog2.models.PlayerChoiceInfo;
import org.labprog2.models.PlayerChoiceRequest;

import java.util.Objects;

public class GameBot {

    public String decideShape(PlayerChoiceRequest request) {
        // Find last decision of the opponent
        String shape = null;
        for(PlayerChoiceInfo playerChoice : request.player_choices) {
            if (!Objects.equals(playerChoice.player_name, request.player_name)) {
                shape = playerChoice.shape;
            }
        }
        // If none was found, set it to the first option
        if (shape == null) {
            shape = request.options.get(0);
        }
        return shape;
    }

}
