package org.labprog2;

import jdk.jshell.spi.ExecutionControl;
import org.labprog2.client.Client;

import java.io.IOException;

public class App
{
    public static void main( String[] args ) throws IOException, ExecutionControl.NotImplementedException {
        Client client = new Client(args[0], args[1], Integer.parseInt(args[2]), true);
        client.requestJoinGame();
    }

}
