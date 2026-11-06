#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Función para imprimir un byte en formato binario
void print_binary(unsigned char byte) {
    for (int i = 7; i >= 0; i--) {
        printf("%c", (byte & (1 << i)) ? '1' : '0');
    }
}

// Programa principal
int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Error: Debe incluir direccion del archivo y tipo de datos a obtener\n 0: Hexadecimal\n 1: Binario\n 2: Texto plano");
        return 1;
    }
    FILE *file;
    int tipo = -1; // 0: hexadecimal - 1: binario
    int bytes_to_read = -1;
    
    for (int i = 0; i < argc; i++)
    {
        if (strcmp(argv[i], "-dir") == 0) {
            // printf("1: caso: %s valor: %s\n", argv[i], argv[i+1] );
            file = fopen(argv[i+1], "rb");
        }
        if (strcmp(argv[i], "-tipo") == 0) {
            // printf("2: caso: %s valor: %s\n", argv[i], argv[i+1] );
            tipo = atoi(argv[i+1]);
        }
        if (strcmp(argv[i], "-bytes") == 0){
            // printf("3: caso: %s valor: %s\n", argv[i], argv[i+1] );
            bytes_to_read = atoi(argv[i+1]);
        }
    }

    tipo = tipo == -1 ? 1 : tipo; // por default Hexadecimal
     
    if (!file) {
        // Error al abrir el archivo
        fprintf(stderr, "Error al abrir el archivo");
        return 1;
    }

    // Mover puntero al final para obtener tamaño
    if (fseek(file, 0, SEEK_END) != 0) {
        fclose(file);
        fprintf(stderr, "Error al mover el puntero del archivo");
        return 1;
    }

    // Leer los bytes
    bytes_to_read = bytes_to_read == -1 ? ftell(file) : bytes_to_read; // Número de bytes del documento
    rewind(file); // nos situamos al inicio del documento

    unsigned char *buffer = (unsigned char*)malloc(bytes_to_read); // variable para almacenar los bytes
    char *data = (char *)malloc(bytes_to_read); // salida

    size_t read_count = fread(buffer, 1, bytes_to_read, file); // averiguar
    
    if (read_count == 0) {
        fclose(file);
        fprintf(stderr, "Error: no se pudo leer el archivo o esta vacio. %d", read_count);
        return 1;
    }

    if (tipo == 1)
    {
        for (size_t i = 0; i < read_count; i++) {
            // if (memcmp(&buffer[i], "/Author", 7) == 0) {
            //     printf("¡Metadato de Autor encontrado en el byte %zu!\n", i);
                
            //     // Imprimir los siguientes bytes para ver el valor del autor
            //     for (int j = 0; j < 30; j++) {
            //         printf("%c", buffer[i + j]);
            //     }
            //     printf("\n");
            // }
            printf("%02X ",buffer[i]);
        }
    }else if (tipo == 2){
        for (size_t i = 0; i < read_count; i++) {
            printf("%c",buffer[i]);
        }
    }else
    {
        for (size_t i = 0; i < read_count; i++) {
            print_binary(buffer[i]);
            printf(" ");
        }
    }
    
    return 0;
}
