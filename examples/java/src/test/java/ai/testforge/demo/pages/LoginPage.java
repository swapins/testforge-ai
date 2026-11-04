package ai.testforge.demo.pages;

import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.WebDriverWait;

public class LoginPage {
    private final WebDriver driver;
    private final WebDriverWait wait;

    private final By usernameField = By.id("username");
    private final By passwordField = By.id("password");
    private final By loginButton = By.id("login");
    private final By statusMessage = By.id("message");

    public LoginPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(5));
    }

    public LoginPage openDemo() {
        var page = getClass().getClassLoader().getResource("demo/login.html");
        if (page == null) {
            throw new IllegalStateException("Demo login page resource was not found.");
        }
        driver.get(page.toExternalForm());
        return this;
    }

    public LoginPage login(String username, String password) {
        driver.findElement(usernameField).clear();
        driver.findElement(usernameField).sendKeys(username);
        driver.findElement(passwordField).clear();
        driver.findElement(passwordField).sendKeys(password);
        driver.findElement(loginButton).click();
        return this;
    }

    public String statusMessage() {
        return wait.until(driver -> driver.findElement(statusMessage).getText());
    }

    public boolean loginButtonIsDisabled() {
        WebElement button = driver.findElement(loginButton);
        return !button.isEnabled();
    }
}
