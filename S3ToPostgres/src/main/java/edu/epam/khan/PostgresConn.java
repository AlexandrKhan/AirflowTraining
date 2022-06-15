package edu.epam.khan;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class PostgresConn {
    public static Connection getConnection() throws SQLException {
        Connection conn = DriverManager.getConnection("jdbc:postgresql://postgres:5432/airflow",
                "airflow", "airflow");
            if (conn != null) {
                System.out.println("Connected to the database!");
                return conn;
            } else {
                System.out.println("Failed to make connection!");
            }
        return null;
    }
}
