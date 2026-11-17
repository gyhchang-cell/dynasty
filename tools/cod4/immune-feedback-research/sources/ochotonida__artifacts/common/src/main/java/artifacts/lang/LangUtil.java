package artifacts.lang;

import com.google.common.base.CaseFormat;
import joptsimple.internal.Strings;

import java.util.List;

public class LangUtil {

    private static final List<String> LOWER_CASE_BY_DEFAULT = List.of(
            "a", "an", "as", "be", "in", "of", "on", "per", "the", "when"
    );

    public static String fromCamelCasedString(String string) {
        return fromSnakeCasedString(CaseFormat.LOWER_CAMEL.to(CaseFormat.LOWER_UNDERSCORE, string));
    }

    public static String fromSnakeCasedString(String string) {
        String[] words = string.split("_");
        for (int i = 0; i < words.length; i++) {
            String word = words[i];
            if (!LOWER_CASE_BY_DEFAULT.contains(word)) {
                words[i] = Character.toUpperCase(word.charAt(0)) + word.substring(1);
            }
        }
        return Strings.join(words, " ");
    }
}
