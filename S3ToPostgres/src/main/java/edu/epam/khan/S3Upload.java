package edu.epam.khan;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.GetObjectRequest;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.S3Object;

import java.io.*;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.zip.GZIPInputStream;



public class S3Upload {
    // Get credentials from env and create AWS Client
    static BasicAWSCredentials awsCreds = new BasicAWSCredentials
            (System.getenv("AWS_ACCESS_KEY"),
                    System.getenv("AWS_SECRET_KEY"));


    static AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
            .withRegion("us-east-1")
            .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
            .build();


    public static void main(String[] args) throws IOException, SQLException {
        String bucketName = args[0];
        String zipName = args[1];
        String csvFile = zipName.substring(0, zipName.lastIndexOf("."));
        String tableName = csvFile.substring(0, csvFile.lastIndexOf("."));

        // Unpack gz from S3
        S3Object object = s3Client.getObject(new GetObjectRequest(bucketName, zipName));
        InputStream objectData = object.getObjectContent();
        GZIPInputStream gzipInputStream = new GZIPInputStream(objectData);
        ObjectMetadata metadata = new ObjectMetadata();
        s3Client.putObject(bucketName, csvFile, gzipInputStream, metadata);
        objectData.close();

        // Create and fill PSQL table from CSV
        S3Object csv_object = s3Client.getObject(new GetObjectRequest(bucketName, csvFile));
        BufferedReader reader = new BufferedReader(new InputStreamReader(csv_object.getObjectContent()));
        String header = reader.readLine();
        List<String> headersWithType = Arrays.stream(header.split(","))
                .map(s -> s + " VARCHAR")
                .collect(Collectors.toList());


        String create_stmt = String.format("CREATE TABLE IF NOT EXISTS %s(%s)", tableName,
                String.join(", ", headersWithType));

        String insert_stmt = String.format("INSERT INTO %s VALUES (%s)", tableName,
                Arrays.stream(header.split(","))
                        .map(v -> "?")
                        .collect(Collectors.joining(", ")));

        Connection conn = PostgresConn.getConnection();
        if (conn != null) {
            PreparedStatement create = conn.prepareStatement(create_stmt);
            create.execute();

            PreparedStatement stmt = conn.prepareStatement(insert_stmt);
            String line;
            while ((line = reader.readLine()) != null) {
                String[] values = line.split(",");
                for (int i = 0; i < values.length; i++) {
                    stmt.setString(i + 1, values[i]);
                }
                stmt.execute();
            }
            conn.close();
        }
    }
}
