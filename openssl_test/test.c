#include <assert.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

unsigned char* hex_string_to_bytes(const char* hex_str) { 
    int hexkey_len = strlen(hex_str);
    assert(hexkey_len % 2 == 0); // Must be even

    int key_len = hexkey_len / 2;
    unsigned char *key = malloc(key_len);
    assert(key != NULL);

    for (int i = 0; i < key_len; i++)
    {
        int n = sscanf(hex_str + 2 * i, "%2hhx", key + i);
        assert(n == 1);
    }

    return key;
}

void print_hmac(const char *hexkey, const char *data)
{
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_len;

    unsigned char *key = hex_string_to_bytes(hexkey);

    HMAC(EVP_sha256(), key, strlen(hexkey) / 2, (const unsigned char *)data, strlen(data),
         digest, &digest_len);

    fputs("HMAC digest: ", stdout);
    for (unsigned int i = 0; i < digest_len; i++)
    {
        printf("%02hhx", digest[i]);
    }
    putchar('\n');
    free(key);
}

int main(void)
{
    char hashString[100];

    puts("echo -n us-east-1|openssl dgst -sha256 -mac HMAC -macopt "
         "hexkey:"
         "b098ff9a24e0573d9e0f952963d0725c4e9c7566ebb3713bf8e0707d43146822");
    puts("  should be: "
         "e811cc78009ad7918504aca1ff987199285352a6fabd1063d6d1a938ac673dbf");
    strcpy(hashString,
           "b098ff9a24e0573d9e0f952963d0725c4e9c7566ebb3713bf8e0707d43146822");
    print_hmac(hashString, "us-east-1");

    puts("echo -n s3|openssl dgst -sha256 -mac HMAC -macopt "
         "hexkey:"
         "e811cc78009ad7918504aca1ff987199285352a6fabd1063d6d1a938ac673dbf");
    puts("  should be: "
         "f405cc5d87cd57f8130decb58108ac0ae5a0bccb97e40729f9ace287d4ee054d");
    strcpy(hashString,
           "e811cc78009ad7918504aca1ff987199285352a6fabd1063d6d1a938ac673dbf");
    print_hmac(hashString, "s3");

    return 0;
}
