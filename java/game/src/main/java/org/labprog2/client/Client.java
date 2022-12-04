package org.labprog2.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.exc.UnrecognizedPropertyException;
import jdk.jshell.spi.ExecutionControl;
import org.labprog2.models.*;

import java.io.*;
import java.net.Socket;

public class Client {
    private final PrintWriter out;
    private final BufferedReader in;
    private final String playerName;
    private final GameBot bot;
    private final boolean isBot;
    static private final ObjectMapper objectMapper = new ObjectMapper();

    public Client(String playerName, String serverHost, int serverPort, boolean isBot) throws IOException {
        Socket clientSocket = new Socket(serverHost, serverPort);
        this.out = new PrintWriter(clientSocket.getOutputStream(), true);
        this.in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
        this.playerName = playerName;
        this.isBot = isBot;
        this.bot = new GameBot();
    }

    public void requestJoinGame() throws IOException, ExecutionControl.NotImplementedException {
        // Send join request
        JoinRequest request = new JoinRequest(this.playerName);
        String requestJson = objectMapper.writeValueAsString(request);
        out.println(requestJson);
        // Receive join response
        String responseJson = in.readLine();
        System.out.println(responseJson);
        // Play game
        playGame();
    }

    public void playGame() throws IOException, ExecutionControl.NotImplementedException {
        while(true) {
            String messageJson = in.readLine();
            System.out.println(messageJson);
            try {
                PlayerChoiceRequest request = objectMapper.readValue(messageJson, PlayerChoiceRequest.class);
                // Choose shape
                String shape = request.options.get(0);
                if(this.isBot) {
                    shape = bot.decideShape(request);
                } else {
                    throw new ExecutionControl.NotImplementedException("User request not implemented");
                }
                // Send response
                PlayerChoiceResponse response =
                        new PlayerChoiceResponse(this.playerName, request.game_id, request.match_number, shape);
                String responseJson = objectMapper.writeValueAsString(response);
                out.println(responseJson);
            } catch (UnrecognizedPropertyException e) {
                EndOfGameMessage message = objectMapper.readValue(messageJson, EndOfGameMessage.class);
                System.out.printf("[END] %s wins", message.winner);
                break;
            }
        }
    }

}
